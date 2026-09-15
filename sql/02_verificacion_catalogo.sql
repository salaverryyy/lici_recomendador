-- Resultado esperado en una sola fila:
-- equipos=22, evaluaciones=22, rangos_radio=25,
-- constelaciones_incorrectas=0, ppp_incoherentes=0,
-- rangos_incorrectos=0, radio_p6h=0, rangos_gs18t=2.
SELECT
    (SELECT COUNT(*) FROM equipos) AS equipos,
    (SELECT COUNT(*) FROM base_evaluacion) AS evaluaciones,
    (SELECT COUNT(*) FROM equipo_radio_frecuencia) AS rangos_radio,
    (SELECT COUNT(*)
       FROM base_evaluacion
      WHERE constelaciones IS DISTINCT FROM
            (gps::int + glonass::int + galileo::int + beidou::int +
             qzss::int + navic_irnss::int)) AS constelaciones_incorrectas,
    (SELECT COUNT(*)
       FROM base_evaluacion
      WHERE tiene_ppp IS DISTINCT FROM
            (ppp_h_cm IS NOT NULL OR ppp_v_cm IS NOT NULL)) AS ppp_incoherentes,
    (SELECT COUNT(*)
       FROM equipo_radio_frecuencia
      WHERE frecuencia_min_mhz > frecuencia_max_mhz) AS rangos_incorrectos,
    (SELECT COUNT(*)
       FROM equipo_radio_frecuencia
      WHERE id_equipo = 'GNSS-SINOGNSS-P6H') AS radio_p6h,
    (SELECT COUNT(*)
       FROM equipo_radio_frecuencia
      WHERE id_equipo = 'GNSS-LEICA-GS18T') AS rangos_gs18t;
