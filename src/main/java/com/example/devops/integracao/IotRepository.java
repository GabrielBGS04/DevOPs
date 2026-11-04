package com.example.devops.integracao;

import org.springframework.data.jpa.repository.JpaRepository;

public interface IotRepository extends JpaRepository<IotEvento, String> { }
