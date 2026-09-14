package com.iplauction.backend.controller;

import com.iplauction.backend.dto.BidResponse;
import com.iplauction.backend.dto.PlaceBidRequest;
import com.iplauction.backend.service.AuctionBidService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auctions")
@RequiredArgsConstructor
public class AuctionBidController {

    private final AuctionBidService auctionBidService;

    @PostMapping("/{auctionId}/bids")
    public BidResponse placeBid(@PathVariable Long auctionId, @Valid @RequestBody PlaceBidRequest request) {

        return auctionBidService.placeBid(
                auctionId,
                request.auctionTeamId()
        );
    }
}