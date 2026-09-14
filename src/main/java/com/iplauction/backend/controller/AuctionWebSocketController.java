package com.iplauction.backend.controller;

import com.iplauction.backend.dto.AuctionLiveStateResponse;
import com.iplauction.backend.dto.PlaceBidRequest;
import com.iplauction.backend.service.AuctionBidService;
import lombok.RequiredArgsConstructor;
import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;

@Controller
@RequiredArgsConstructor
public class AuctionWebSocketController {

    private final AuctionBidService auctionBidService;
    private final SimpMessagingTemplate messagingTemplate;

    @MessageMapping("/auction/{auctionId}/bid")
    public void placeBid(@DestinationVariable Long auctionId, PlaceBidRequest request) {

        auctionBidService.placeBid(auctionId, request.auctionTeamId());

        AuctionLiveStateResponse liveState = auctionBidService.getLiveState(auctionId);

        messagingTemplate.convertAndSend("/topic/auction/" + auctionId, liveState);
    }
}