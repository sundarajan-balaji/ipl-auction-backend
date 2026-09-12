package com.iplauction.backend.service;

import com.iplauction.backend.dto.AuctionTeamResponse;
import com.iplauction.backend.entity.Auction;
import com.iplauction.backend.entity.AuctionTeam;
import com.iplauction.backend.entity.Team;
import com.iplauction.backend.exception.DuplicateResourceException;
import com.iplauction.backend.exception.ResourceNotFoundException;
import com.iplauction.backend.repository.AuctionRepository;
import com.iplauction.backend.repository.AuctionTeamRepository;
import com.iplauction.backend.repository.TeamRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AuctionTeamService {

    private final AuctionRepository auctionRepository;
    private final TeamRepository teamRepository;
    private final AuctionTeamRepository auctionTeamRepository;

    public AuctionTeamResponse addTeamToAuction(Long auctionId, Long teamId) {
        Auction auction = auctionRepository.findById(auctionId)
                .orElseThrow(() -> new ResourceNotFoundException("Auction not found with id: " + auctionId));

        Team team = teamRepository.findById(teamId)
                .orElseThrow(() -> new ResourceNotFoundException("Team not found with id: " + teamId));

        if (auctionTeamRepository.existsByAuctionIdAndTeamId(auctionId, teamId)) {
            throw new DuplicateResourceException(
                    "Team is already participating in this auction"
            );
        }

        AuctionTeam auctionTeam = AuctionTeam.builder()
                .auction(auction)
                .team(team)
                .startingPurse(auction.getStartingPurse())
                .remainingPurse(auction.getStartingPurse())
                .build();

        AuctionTeam savedAuctionTeam = auctionTeamRepository.save(auctionTeam);

        return toResponse(savedAuctionTeam);
    }

    public List<AuctionTeamResponse> getTeamsForAuction(Long auctionId) {

        if (!auctionRepository.existsById(auctionId)) {
            throw new ResourceNotFoundException("Auction not found with id: " + auctionId);
        }

        return auctionTeamRepository.findByAuctionId(auctionId)
                .stream()
                .map(this::toResponse)
                .toList();
    }

    private AuctionTeamResponse toResponse(AuctionTeam auctionTeam) {
        return new AuctionTeamResponse(
                auctionTeam.getId(),
                auctionTeam.getAuction().getId(),
                auctionTeam.getTeam().getId(),
                auctionTeam.getTeam().getName(),
                auctionTeam.getTeam().getShortCode(),
                auctionTeam.getStartingPurse(),
                auctionTeam.getRemainingPurse()
        );
    }
}