package com.iplauction.backend.service;

import com.iplauction.backend.dto.AuctionResponse;
import com.iplauction.backend.entity.Auction;
import com.iplauction.backend.exception.ResourceNotFoundException;
import com.iplauction.backend.repository.AuctionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AuctionService {

    private final AuctionRepository auctionRepository;

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