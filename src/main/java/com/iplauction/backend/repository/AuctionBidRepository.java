package com.iplauction.backend.repository;

import com.iplauction.backend.entity.AuctionBid;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface AuctionBidRepository extends JpaRepository<AuctionBid, Long> {
    Optional<AuctionBid> findFirstByAuctionPlayerIdOrderByAmountDesc(Long auctionPlayerId);
}