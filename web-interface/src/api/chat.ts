import { io } from 'socket.io-client';

const SOCKET_URL = '/';

export const socket = io(SOCKET_URL);
