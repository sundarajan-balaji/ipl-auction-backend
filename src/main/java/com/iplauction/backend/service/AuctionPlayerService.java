package com.iplauction.backend.service;

import com.iplauction.backend.dto.AuctionPlayerResponse;
import com.iplauction.backend.entity.Auction;
import com.iplauction.backend.entity.AuctionPlayer;
import com.iplauction.backend.entity.Player;
import com.iplauction.backend.exception.DuplicateResourceException;
import com.iplauction.backend.exception.ResourceNotFoundException;
import com.iplauction.backend.repository.AuctionPlayerRepository;
import com.iplauction.backend.repository.AuctionRepository;
import com.iplauction.backend.repository.PlayerRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AuctionPlayerService {

    private final AuctionRepository auctionRepository;
    private final PlayerRepository playerRepository;
    private final AuctionPlayerRepository auctionPlayerRepository;

    public AuctionPlayerResponse addPlayerToAuction(Long auctionId, Long playerId, Long basePrice) {
        Auction auction = auctionRepository.findById(auctionId)
                .orElseThrow(() -> new ResourceNotFoundException("Auction not found with id: " + auctionId));

        Player player = playerRepository.findById(playerId)
                .orElseThrow(() -> new ResourceNotFoundException("Player not found with id: " + playerId));

        if (auctionPlayerRepository.existsByAuctionIdAndPlayerId(auctionId, playerId)) {
            throw new DuplicateResourceException("Player is already participating in this auction");
        }

        AuctionPlayer auctionPlayer = AuctionPlayer.builder()
                .auction(auction)
                .player(player)
                .basePrice(basePrice)
                .status("REGISTERED")
                .soldToAuctionTeam(null)
                .soldPrice(null)
                .build();

        AuctionPlayer savedAuctionPlayer = auctionPlayerRepository.save(auctionPlayer);
        return toResponse(savedAuctionPlayer);
    }

    public List<AuctionPlayerResponse> getPlayersForAuction(Long auctionId) {

        if (!auctionRepository.existsById(auctionId)) {
            throw new ResourceNotFoundException("Auction not found with id: " + auctionId);
        }

        return auctionPlayerRepository.findByAuctionId(auctionId)
                .stream()
                .map(this::toResponse)
                .toList();
    }

    private AuctionPlayerResponse toResponse(AuctionPlayer auctionPlayer) {
        return new AuctionPlayerResponse(
                auctionPlayer.getId(),
                auctionPlayer.getAuction().getId(),
                auctionPlayer.getPlayer().getId(),
                auctionPlayer.getPlayer().getName(),
                auctionPlayer.getBasePrice(),
                auctionPlayer.getStatus(),
                auctionPlayer.getSoldToAuctionTeam() != null
                        ? auctionPlayer.getSoldToAuctionTeam().getId()
                        : null,
                auctionPlayer.getSoldPrice()
        );
    }
}