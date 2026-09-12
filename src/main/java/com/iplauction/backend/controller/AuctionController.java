package com.iplauction.backend.controller;

import com.iplauction.backend.dto.AuctionResponse;
import com.iplauction.backend.dto.CreateAuctionRequest;
import com.iplauction.backend.service.AuctionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/auctions")
@RequiredArgsConstructor
public class AuctionController {

    private final AuctionService auctionService;

    @PostMapping
    public AuctionResponse createAuction(@Valid @RequestBody CreateAuctionRequest request) {
        return auctionService.createAuction(
                request.name(),
                request.season(),
                request.startingPurse()
        );
    }

    @GetMapping
    public List<AuctionResponse> getAllAuctions() {
        return auctionService.getAllAuctions();
    }

    @GetMapping("/{id}")
    public AuctionResponse getAuctionById(@PathVariable Long id) {
        return auctionService.getAuctionById(id);
    }
}