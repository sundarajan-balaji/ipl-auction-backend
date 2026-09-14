package com.iplauction.backend.repository;

import com.iplauction.backend.entity.AuctionPlayer;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface AuctionPlayerRepository extends JpaRepository<AuctionPlayer, Long> {

    boolean existsByAuctionIdAndPlayerId(Long auctionId, Long playerId);
    List<AuctionPlayer> findByAuctionId(Long auctionId);
    long countByAuctionId(Long auctionId);

    @Query("""
        SELECT COALESCE(MAX(ap.auctionOrder), 0)
        FROM AuctionPlayer ap
        WHERE ap.auction.id = :auctionId
        """)
    int findMaxAuctionOrderByAuctionId(@Param("auctionId") Long auctionId);

    Optional<AuctionPlayer> findFirstByAuctionIdAndStatusOrderByAuctionOrderAsc(
            Long auctionId,
            String status
    );
}