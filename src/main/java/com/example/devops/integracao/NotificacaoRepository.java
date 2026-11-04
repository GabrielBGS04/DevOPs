package com.example.devops.integracao;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface NotificacaoRepository extends JpaRepository<NotificacaoEvento, String> {
    List<NotificacaoEvento> findTop50ByEntregueFalseOrderByEventIdAsc();
    long countByEntregueFalse();
}
