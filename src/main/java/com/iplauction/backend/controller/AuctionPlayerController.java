package com.iplauction.backend.controller;

import com.iplauction.backend.dto.AddAuctionPlayerRequest;
import com.iplauction.backend.dto.AuctionPlayerResponse;
import com.iplauction.backend.service.AuctionPlayerService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/auctions/{auctionId}/players")
@RequiredArgsConstructor
public class AuctionPlayerController {

    private final AuctionPlayerService auctionPlayerService;

    @PostMapping
    public AuctionPlayerResponse addPlayerToAuction(@PathVariable Long auctionId, @Valid @RequestBody AddAuctionPlayerRequest request) {
        return auctionPlayerService.addPlayerToAuction(
                auctionId,
                request.playerId(),
                request.basePrice()
        );
    }

    @GetMapping
    public List<AuctionPlayerResponse> getPlayersForAuction(@PathVariable Long auctionId) {
        return auctionPlayerService.getPlayersForAuction(auctionId);
    }
}