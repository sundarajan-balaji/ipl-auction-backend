package com.iplauction.backend.service;

import com.iplauction.backend.entity.User;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.client.oidc.userinfo.OidcUserRequest;
import org.springframework.security.oauth2.client.oidc.userinfo.OidcUserService;
import org.springframework.security.oauth2.core.oidc.user.OidcUser;
import org.springframework.security.oauth2.core.oidc.user.DefaultOidcUser;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.Set;

@Service
@RequiredArgsConstructor
public class CustomOidcUserService extends OidcUserService {

    private final UserService userService;

    @Override
    public OidcUser loadUser(OidcUserRequest userRequest) {

        OidcUser oidcUser = super.loadUser(userRequest);

        User user = userService.processOAuthUser(oidcUser);

        Set<SimpleGrantedAuthority> authorities = new HashSet<>();

        authorities.addAll(
                oidcUser.getAuthorities()
                        .stream()
                        .map(authority ->
                                new SimpleGrantedAuthority(
                                        authority.getAuthority()
                                ))
                        .toList()
        );

        authorities.add(
                new SimpleGrantedAuthority(
                        "ROLE_" + user.getRole().name()
                )
        );

        return new DefaultOidcUser(
                authorities,
                oidcUser.getIdToken(),
                oidcUser.getUserInfo(),
                "sub"
        );
    }
}