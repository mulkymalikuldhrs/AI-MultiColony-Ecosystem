
import { BrowserFS } from "./file_system";

export type AuditLayer = 'MARKET' | 'SENSOR' | 'PRESSURE' | 'DECISION' | 'RISK' | 'EXECUTION' | 'SYSTEM';

export interface AuditEntry {
    timestamp: number;
    layer: AuditLayer;
    event: string;
    data: unknown;
    status: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
}

const MAX_LOGS = 1000;
let logs: AuditEntry[] = [];

export const AuditLogger = {
    log: (layer: AuditLayer, event: string, data: unknown = {}, status: AuditEntry['status'] = 'INFO') => {
        const entry: AuditEntry = {
            timestamp: Date.now(),
            layer,
            event,
            data,
            status
        };
        
        logs.unshift(entry);
        if (logs.length > MAX_LOGS) logs = logs.slice(0, MAX_LOGS);
        
        // Persist to local storage via BrowserFS if possible, or console for now
        console.log(`[AUDIT][${layer}][${status}] ${event}`, data);
        
        // Save to system audit log file in memory (mocking persistence)
        try {
            const currentAudit = BrowserFS.loadFile('system_audit_trail.json') || [];
            currentAudit.unshift(entry);
            BrowserFS.saveFile('system_audit_trail.json', currentAudit.slice(0, MAX_LOGS));
        } catch (e) {
            // Silently fail if FS is not ready
        }
    },

    getLogs: (filter?: { layer?: AuditLayer; status?: AuditEntry['status'] }): AuditEntry[] => {
        let filtered = [...logs];
        if (filter?.layer) filtered = filtered.filter(l => l.layer === filter.layer);
        if (filter?.status) filtered = filtered.filter(l => l.status === filter.status);
        return filtered;
    },

    clear: () => {
        logs = [];
        BrowserFS.saveFile('system_audit_trail.json', []);
    }
};
