package com.iplauction.backend.service;

import com.iplauction.backend.dto.AuctionLiveStateResponse;
import com.iplauction.backend.dto.BidResponse;
import com.iplauction.backend.entity.Auction;
import com.iplauction.backend.entity.AuctionBid;
import com.iplauction.backend.entity.AuctionPlayer;
import com.iplauction.backend.entity.AuctionTeam;
import com.iplauction.backend.exception.InvalidAuctionStateException;
import com.iplauction.backend.exception.ResourceNotFoundException;
import com.iplauction.backend.repository.AuctionBidRepository;
import com.iplauction.backend.repository.AuctionRepository;
import com.iplauction.backend.repository.AuctionTeamRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.OffsetDateTime;

@Service
@RequiredArgsConstructor
public class AuctionBidService {

    private final AuctionRepository auctionRepository;
    private final AuctionTeamRepository auctionTeamRepository;
    private final AuctionBidRepository auctionBidRepository;

    @PreAuthorize("hasAnyRole('ADMIN', 'AUCTIONEER', 'TEAM_USER')")
    @Transactional
    public BidResponse placeBid(Long auctionId, Long auctionTeamId) {

        Auction auction = auctionRepository.findByIdForUpdate(auctionId)
                .orElseThrow(() -> new ResourceNotFoundException("Auction not found with id: " + auctionId));

        if (!auction.getStatus().equals("LIVE")) {
            throw new InvalidAuctionStateException("Bids can only be placed when auction is LIVE");
        }

        AuctionPlayer currentPlayer = auction.getCurrentPlayer();

        if (currentPlayer == null) {
            throw new InvalidAuctionStateException("No player is currently being auctioned");
        }

        AuctionTeam auctionTeam = auctionTeamRepository.findById(auctionTeamId)
                .orElseThrow(() -> new ResourceNotFoundException("Auction team not found with id: " + auctionTeamId));

        if (!auctionTeam.getAuction().getId().equals(auctionId)) {
            throw new InvalidAuctionStateException("Team is not participating in this auction");
        }

        AuctionBid highestBid = auctionBidRepository.findFirstByAuctionPlayerIdOrderByAmountDesc(currentPlayer.getId()).orElse(null);

        long bidAmount;

        if (highestBid == null) {
            bidAmount = currentPlayer.getBasePrice();
        } else {
            bidAmount = highestBid.getAmount() + auction.getBidIncrement();
        }

        if (bidAmount > auctionTeam.getRemainingPurse()) {
            throw new InvalidAuctionStateException(
                    "Team does not have enough remaining purse"
            );
        }

        AuctionBid bid = AuctionBid.builder()
                .auction(auction)
                .auctionPlayer(currentPlayer)
                .auctionTeam(auctionTeam)
                .amount(bidAmount)
                .build();

        AuctionBid savedBid = auctionBidRepository.save(bid);

        return toResponse(savedBid);
    }

    public AuctionLiveStateResponse getLiveState(Long auctionId) {

        Auction auction = auctionRepository.findById(auctionId)
                .orElseThrow(() -> new ResourceNotFoundException("Auction not found with id: " + auctionId));

        if (!auction.getStatus().equals("LIVE")) {
            throw new InvalidAuctionStateException("Live state is only available when auction is LIVE");
        }

        AuctionPlayer currentPlayer = auction.getCurrentPlayer();

        if (currentPlayer == null) {
            throw new InvalidAuctionStateException("No player is currently being auctioned");
        }

        AuctionBid highestBid = auctionBidRepository.findFirstByAuctionPlayerIdOrderByAmountDesc(currentPlayer.getId()).orElse(null);

        Long currentBid;
        Long highestBidderTeamId;
        String highestBidderTeamName;

        if (highestBid == null) {
            currentBid = currentPlayer.getBasePrice();
            highestBidderTeamId = null;
            highestBidderTeamName = null;
        } else {
            currentBid = highestBid.getAmount();
            highestBidderTeamId = highestBid.getAuctionTeam().getId();
            highestBidderTeamName = highestBid.getAuctionTeam().getTeam().getName();
        }

        return new AuctionLiveStateResponse(
                auction.getId(),
                currentPlayer.getId(),
                currentPlayer.getPlayer().getName(),
                currentPlayer.getBasePrice(),
                currentBid,
                highestBidderTeamId,
                highestBidderTeamName,
                auction.getBidIncrement(),
                currentPlayer.getStatus(),
                OffsetDateTime.now()
        );
    }

    private BidResponse toResponse(AuctionBid bid) {
        return new BidResponse(
                bid.getId(),
                bid.getAuction().getId(),
                bid.getAuctionPlayer().getId(),
                bid.getAuctionTeam().getId(),
                bid.getAmount(),
                bid.getCreatedAt()
        );
    }
}