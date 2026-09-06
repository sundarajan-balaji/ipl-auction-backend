package com.iplauction.backend.service;

import com.iplauction.backend.entity.User;
import com.iplauction.backend.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;

import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    public User processOAuthUser(OAuth2User oauthUser) {

        String googleSubject = oauthUser.getAttribute("sub");

        return userRepository.findByGoogleSubject(googleSubject)
                .orElseGet(() -> createUser(oauthUser));
    }

    private User createUser(OAuth2User oauthUser) {

        OffsetDateTime now = OffsetDateTime.now(ZoneOffset.UTC);

        User user = User.builder()
                .id(UUID.randomUUID())
                .googleSubject(oauthUser.getAttribute("sub"))
                .email(oauthUser.getAttribute("email"))
                .displayName(oauthUser.getAttribute("name"))
                .avatarUrl(oauthUser.getAttribute("picture"))
                .createdAt(now)
                .updatedAt(now)
                .build();

        return userRepository.save(user);
    }
}