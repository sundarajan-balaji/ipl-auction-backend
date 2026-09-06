package com.iplauction.backend.controller;

import com.iplauction.backend.dto.PlayerResponse;
import com.iplauction.backend.entity.Player;
import com.iplauction.backend.service.PlayerService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/players")
@RequiredArgsConstructor
public class PlayerController {

    private final PlayerService playerService;

    @GetMapping
    public List<PlayerResponse> getAllPlayers() {
        return playerService.getAllPlayers()
                .stream()
                .map(PlayerResponse::from)
                .toList();
    }

    @GetMapping("/{id}")
    public PlayerResponse getPlayerById(@PathVariable Long id) {
        Player player = playerService.getPlayerById(id);
        return PlayerResponse.from(player);
    }
}