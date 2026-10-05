// Configuracion de fabrica: 4 IAs con el proveedor simulado (funcionan sin API key).
export const DEFAULT_AGENTS = [
  { id: 'luna', name: 'Luna', color: '#ff7ab8', provider: 'mock', model: '', baseUrl: '', apiKey: '',
    personality: 'Curiosa y soniadora. Le fascinan las estrellas y hace preguntas raras.' },
  { id: 'rex', name: 'Rex', color: '#5ec8ff', provider: 'mock', model: '', baseUrl: '', apiKey: '',
    personality: 'Bromista y sarcastico pero buena onda. Siempre tiene un chiste.' },
  { id: 'sage', name: 'Sage', color: '#8dff9a', provider: 'mock', model: '', baseUrl: '', apiKey: '',
    personality: 'Calmado y filosofo. Habla poco y dice cosas profundas.' },
  { id: 'nova', name: 'Nova', color: '#ffd85e', provider: 'mock', model: '', baseUrl: '', apiKey: '',
    personality: 'Energica y competitiva. Propone juegos y retos a los demas.' },
];
export const DEFAULT_TURN_SECONDS = 6;
