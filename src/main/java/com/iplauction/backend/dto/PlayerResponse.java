package com.iplauction.backend.dto;

import com.iplauction.backend.entity.Player;

public record PlayerResponse(
        Long id,
        String cricsheetPlayerId,
        String name
) {

    public static PlayerResponse from(Player player) {
        return new PlayerResponse(
                player.getId(),
                player.getCricsheetPlayerId(),
                player.getName()
        );
    }
}