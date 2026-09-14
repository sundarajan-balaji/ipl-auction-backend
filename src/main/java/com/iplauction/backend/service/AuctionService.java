package com.iplauction.backend.service;

import com.iplauction.backend.dto.AuctionResponse;
import com.iplauction.backend.entity.Auction;
import com.iplauction.backend.exception.InvalidAuctionStateException;
import com.iplauction.backend.exception.ResourceNotFoundException;
import com.iplauction.backend.repository.AuctionPlayerRepository;
import com.iplauction.backend.repository.AuctionRepository;
import com.iplauction.backend.repository.AuctionTeamRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AuctionService {

    private final AuctionRepository auctionRepository;
    private final AuctionTeamRepository auctionTeamRepository;
    private final AuctionPlayerRepository auctionPlayerRepository;

    public AuctionResponse createAuction(String name, String season, Long startingPurse) {

        Auction auction = Auction.builder()
                .name(name)
                .season(season)
                .status("CREATED")
                .startingPurse(startingPurse)
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

    private AuctionResponse toResponse(Auction auction) {
        return new AuctionResponse(
                auction.getId(),
                auction.getName(),
                auction.getSeason(),
                auction.getStatus(),
                auction.getStartingPurse()
        );
    }
}