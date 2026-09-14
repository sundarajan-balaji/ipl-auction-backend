package com.iplauction.backend.service;

import com.iplauction.backend.dto.AuctionResponse;
import com.iplauction.backend.entity.Auction;
import com.iplauction.backend.entity.AuctionBid;
import com.iplauction.backend.entity.AuctionPlayer;
import com.iplauction.backend.entity.AuctionTeam;
import com.iplauction.backend.exception.InvalidAuctionStateException;
import com.iplauction.backend.exception.ResourceNotFoundException;
import com.iplauction.backend.repository.AuctionBidRepository;
import com.iplauction.backend.repository.AuctionPlayerRepository;
import com.iplauction.backend.repository.AuctionRepository;
import com.iplauction.backend.repository.AuctionTeamRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AuctionService {

    private final AuctionRepository auctionRepository;
    private final AuctionTeamRepository auctionTeamRepository;
    private final AuctionPlayerRepository auctionPlayerRepository;
    private final AuctionBidRepository auctionBidRepository;

    @PreAuthorize("hasRole('ADMIN')")
    public AuctionResponse createAuction(
            String name,
            String season,
            Long startingPurse,
            Long bidIncrement)  {

        Auction auction = Auction.builder()
                .name(name)
                .season(season)
                .status("CREATED")
                .startingPurse(startingPurse)
                .bidIncrement(bidIncrement)
                .build();

        Auction savedAuction = auctionRepository.save(auction);

        return toResponse(savedAuction);
    }

    public List<AuctionResponse> getAllAuctions() {
        return auctionRepository.findAll()
                .stream()
                .map(this::toResponse)
                .toList();
    }

    public AuctionResponse getAuctionById(Long id) {
        Auction auction = auctionRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Auction not found with id: " + id));

        return toResponse(auction);
    }

    @PreAuthorize("hasRole('ADMIN')")
    public AuctionResponse markAuctionReady(Long auctionId) {

        Auction auction = auctionRepository.findById(auctionId)
                .orElseThrow(() -> new ResourceNotFoundException("Auction not found with id: " + auctionId));

        if (!auction.getStatus().equals("CREATED")) {
            throw new InvalidAuctionStateException("Auction can only be marked READY from CREATED status");
        }

        long teamCount = auctionTeamRepository.countByAuctionId(auctionId);

        if (teamCount == 0) {
            throw new InvalidAuctionStateException("Auction must have at least one participating team");
        }

        long playerCount = auctionPlayerRepository.countByAuctionId(auctionId);

        if (playerCount == 0) {
            throw new InvalidAuctionStateException("Auction must have at least one participating player");
        }

        auction.setStatus("READY");
        Auction savedAuction = auctionRepository.save(auction);
        return toResponse(savedAuction);
    }

    @PreAuthorize("hasAnyRole('ADMIN', 'AUCTIONEER')")
    public AuctionResponse startAuction(Long auctionId) {

        Auction auction = auctionRepository.findById(auctionId)
                .orElseThrow(() -> new ResourceNotFoundException("Auction not found with id: " + auctionId));

        if (!auction.getStatus().equals("READY")) {
            throw new InvalidAuctionStateException("Auction can only be started from READY status");
        }

        auction.setStatus("LIVE");
        Auction savedAuction = auctionRepository.save(auction);
        return toResponse(savedAuction);
    }

    @PreAuthorize("hasAnyRole('ADMIN', 'AUCTIONEER')")
    public AuctionResponse completeAuction(Long auctionId) {

        Auction auction = auctionRepository.findById(auctionId)
                .orElseThrow(() -> new ResourceNotFoundException("Auction not found with id: " + auctionId));

        if (!auction.getStatus().equals("LIVE")) {
            throw new InvalidAuctionStateException("Auction can only be completed from LIVE status");
        }

        auction.setStatus("COMPLETED");
        Auction savedAuction = auctionRepository.save(auction);
        return toResponse(savedAuction);
    }

    @PreAuthorize("hasAnyRole('ADMIN', 'AUCTIONEER')")
    public AuctionResponse moveToNextPlayer(Long auctionId) {

        Auction auction = auctionRepository.findById(auctionId)
                .orElseThrow(() -> new ResourceNotFoundException("Auction not found with id: " + auctionId));

        if (!auction.getStatus().equals("LIVE")) {
            throw new InvalidAuctionStateException("Next player can only be selected when auction is LIVE");
        }

        AuctionPlayer nextPlayer =
                auctionPlayerRepository
                        .findFirstByAuctionIdAndStatusOrderByAuctionOrderAsc(auctionId, "REGISTERED")
                        .orElseThrow(() -> new InvalidAuctionStateException("No registered players remaining"));

        auction.setCurrentPlayer(nextPlayer);
        Auction savedAuction = auctionRepository.save(auction);
        return toResponse(savedAuction);
    }

    @PreAuthorize("hasAnyRole('ADMIN', 'AUCTIONEER')")
    @Transactional
    public AuctionResponse sellCurrentPlayer(Long auctionId) {

        Auction auction = auctionRepository.findById(auctionId)
                .orElseThrow(() -> new ResourceNotFoundException("Auction not found with id: " + auctionId));

        if (!auction.getStatus().equals("LIVE")) {
            throw new InvalidAuctionStateException("Player can only be sold when auction is LIVE");
        }

        AuctionPlayer currentPlayer = auction.getCurrentPlayer();

        if (currentPlayer == null) {
            throw new InvalidAuctionStateException("No player is currently being auctioned");
        }

        if (!currentPlayer.getStatus().equals("REGISTERED")) {
            throw new InvalidAuctionStateException("Current player has already been processed");
        }

        AuctionBid highestBid = auctionBidRepository
                        .findFirstByAuctionPlayerIdOrderByAmountDesc(currentPlayer.getId())
                        .orElseThrow(() -> new InvalidAuctionStateException("Cannot sell player because no bids were placed"));

        AuctionTeam winningTeam = highestBid.getAuctionTeam();

        if (highestBid.getAmount() > winningTeam.getRemainingPurse()) {
            throw new InvalidAuctionStateException(
                    "Winning team does not have enough remaining purse"
            );
        }

        currentPlayer.setStatus("SOLD");
        currentPlayer.setSoldToAuctionTeam(winningTeam);
        currentPlayer.setSoldPrice(highestBid.getAmount());

        winningTeam.setRemainingPurse(winningTeam.getRemainingPurse() - highestBid.getAmount());

        auctionPlayerRepository.save(currentPlayer);
        auctionTeamRepository.save(winningTeam);

        return toResponse(auction);
    }

    @PreAuthorize("hasAnyRole('ADMIN', 'AUCTIONEER')")
    @Transactional
    public AuctionResponse markCurrentPlayerUnsold(Long auctionId) {

        Auction auction = auctionRepository.findById(auctionId)
                .orElseThrow(() -> new ResourceNotFoundException("Auction not found with id: " + auctionId));

        if (!auction.getStatus().equals("LIVE")) {
            throw new InvalidAuctionStateException("Player can only be marked UNSOLD when auction is LIVE");
        }

        AuctionPlayer currentPlayer = auction.getCurrentPlayer();

        if (currentPlayer == null) {
            throw new InvalidAuctionStateException("No player is currently being auctioned");
        }

        if (!currentPlayer.getStatus().equals("REGISTERED")) {
            throw new InvalidAuctionStateException("Current player has already been processed");
        }

        currentPlayer.setStatus("UNSOLD");
        auctionPlayerRepository.save(currentPlayer);
        return toResponse(auction);
    }

    private AuctionResponse toResponse(Auction auction) {

        AuctionPlayer currentPlayer = auction.getCurrentPlayer();

        return new AuctionResponse(
                auction.getId(),
                auction.getName(),
                auction.getSeason(),
                auction.getStatus(),
                auction.getStartingPurse(),
                auction.getBidIncrement(),

                currentPlayer != null ? currentPlayer.getId() : null,
                currentPlayer != null ? currentPlayer.getPlayer().getName() : null,
                currentPlayer != null ? currentPlayer.getBasePrice() : null,
                currentPlayer != null ? currentPlayer.getStatus() : null
        );
    }
}