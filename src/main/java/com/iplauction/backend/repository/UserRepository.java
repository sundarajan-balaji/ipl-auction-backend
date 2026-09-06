package com.iplauction.backend.repository;

import com.iplauction.backend.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface UserRepository extends JpaRepository<User, UUID> {
    Optional<User> findByGoogleSubject(String googleSubject);
    Optional<User> findByEmail(String email);
}
