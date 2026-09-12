package com.iplauction.backend.repository;

import com.iplauction.backend.entity.AuctionTeam;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface AuctionTeamRepository extends JpaRepository<AuctionTeam, Long> {
    boolean existsByAuctionIdAndTeamId(Long auctionId, Long teamId);
    List<AuctionTeam> findByAuctionId(Long auctionId);
}