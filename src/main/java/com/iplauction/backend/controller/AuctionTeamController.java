package com.iplauction.backend.controller;

import com.iplauction.backend.dto.AddAuctionTeamRequest;
import com.iplauction.backend.dto.AuctionTeamResponse;
import com.iplauction.backend.service.AuctionTeamService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/auctions/{auctionId}/teams")
@RequiredArgsConstructor
public class AuctionTeamController {

    private final AuctionTeamService auctionTeamService;

    @PostMapping
    public AuctionTeamResponse addTeamToAuction(@PathVariable Long auctionId, @Valid @RequestBody AddAuctionTeamRequest request) {
        return auctionTeamService.addTeamToAuction(
                auctionId,
                request.teamId()
        );
    }

    @GetMapping
    public List<AuctionTeamResponse> getTeamsForAuction(@PathVariable Long auctionId) {
        return auctionTeamService.getTeamsForAuction(auctionId);
    }
}