import { create } from "zustand";

interface AppState {
  sidebarOpen: boolean;
  activePage: string;
  wsConnected: boolean;
  eventFeed: Array<{
    id: string;
    type: string;
    message: string;
    timestamp: string;
    severity: string;
  }>;

  // Actions
  toggleSidebar: () => void;
  setActivePage: (page: string) => void;
  setWsConnected: (connected: boolean) => void;
  addEvent: (event: {
    id: string;
    type: string;
    message: string;
    timestamp: string;
    severity: string;
  }) => void;
  clearEvents: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: true,
  activePage: "dashboard",
  wsConnected: false,
  eventFeed: [],

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setActivePage: (page) => set({ activePage: page }),
  setWsConnected: (connected) => set({ wsConnected: connected }),
  addEvent: (event) =>
    set((state) => ({
      eventFeed: [event, ...state.eventFeed].slice(0, 100),
    })),
  clearEvents: () => set({ eventFeed: [] }),
}));
