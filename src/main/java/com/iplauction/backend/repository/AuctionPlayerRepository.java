package com.iplauction.backend.repository;

import com.iplauction.backend.entity.AuctionPlayer;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface AuctionPlayerRepository extends JpaRepository<AuctionPlayer, Long> {

    boolean existsByAuctionIdAndPlayerId(Long auctionId, Long playerId);
    List<AuctionPlayer> findByAuctionId(Long auctionId);
    long countByAuctionId(Long auctionId);
}