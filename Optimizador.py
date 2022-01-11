def optimizador(df):


  decision_rutas = []       # va a almacenar el estado de cada ruta en funcion de si cumple las reglas: desechada o candidata
  for i in df.index:        # condiciones de las reglas correspondientes al primer nivel
    if (df['lim_bw'][i] < 5000  or  df['lost_percent'][i] > 0.5  or  df['jitter_ms'][i] > 0.05  or  df['throughput_mbps'][i] < 5):
      decision_rutas.append('ruta_desechada')
    else:
      decision_rutas.append('ruta_candidata')

  b = 0                      # si ninguna ruta cumple las condiciones, se devuelve el siguiente mensaje
  for i in range(len(decision_rutas)):
    if (decision_rutas[i] == 'ruta_desechada'):
      b = b+1
  if (df.shape[0] == b):
    print("Ninguna ruta cumple los requisitos mínimos correspondientes a las reglas del primer nivel")
    return

  valores_max = df.max()     # se almacenan los valores maximo y minimo de cada metrica para 
  valores_min = df.min()     # utilizarlos en las reglas correspondientes al segundo nivel
  
  for i in df.index:         #regla correspondiente al ancho de banda
    if (df['lim_bw'][i] !=  valores_max['lim_bw'] and  decision_rutas[i] == 'ruta_candidata'):
      decision_rutas[i] = 'ruta_desechada'    #se desechan las reglas que no cumplen la primera regla del segundo nivel
  l, b = np.unique(decision_rutas, return_counts=True)
  if (b[0] == 1):
    for i in range(len(decision_rutas)):
      if decision_rutas[i] == 'ruta_candidata':
        ruta_elegida = df.iloc[i]              #si solo queda una ruta candidata con ancho de banda maximo
        return ruta_elegida['remote_host']     # se elige esa ruta
  else:
    for i in df.index:       #regla correspondiente al porcentaje de perdidas
      if (df['lost_percent'][i] !=  valores_min['lost_percent'] and  decision_rutas[i] == 'ruta_candidata'):
        decision_rutas[i] = 'ruta_desechada'
    l, b = np.unique(decision_rutas, return_counts=True)
    if (b[0] == 1):
      for i in range(len(decision_rutas)):
        if decision_rutas[i] == 'ruta_candidata': 
          ruta_elegida = df.iloc[i]                 #si solo queda una ruta candidata con porcentaje 
          return ruta_elegida['remote_host']        #de perdidas minimo se selecciona
    else:
      for i in df.index:      #regla correspondiente al jitter
        if (df['jitter_ms'][i] !=  valores_min['jitter_ms'] and  decision_rutas[i] == 'ruta_candidata'):
          decision_rutas[i] = 'ruta_desechada'
      l, b = np.unique(decision_rutas, return_counts=True)
      if (b[0] == 1):
        for i in range(len(decision_rutas)):
          if decision_rutas[i] == 'ruta_candidata':
            ruta_elegida = df.iloc[i]                 #si solo queda una ruta candidata con jitter minimo
            return ruta_elegida['remote_host']        #se selecciona
      else:
        for i in df.index:    #regla correspondiente al throughput
          if (df['throughput_mbps'][i] !=  valores_max['throughput_mbps'] and  decision_rutas[i] == 'ruta_candidata'):
            decision_rutas[i] = 'ruta_desechada'
        l, b = np.unique(decision_rutas, return_counts=True)
        if (b[0] == 1):
          for i in range(len(decision_rutas)):
            if decision_rutas[i] == 'ruta_candidata':
              ruta_elegida = df.iloc[i]               #si solo queda una ruta candidata con throughput
              return ruta_elegida['remote_host']      #maximo se selecciona
        else:
          for i in df.index:  #regla correspondiente al numero de saltos
            if (df['numero_saltos'][i] ==  valores_min['numero_saltos'] and  decision_rutas[i] == 'ruta_candidata'):
              ruta_elegida = df.iloc[i]               #se selecciona la ruta entre las candidatas restantes
              return ruta_elegida['remote_host']      #con menor numero de saltos