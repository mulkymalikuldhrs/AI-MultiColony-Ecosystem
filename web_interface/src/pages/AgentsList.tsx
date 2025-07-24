import React from 'react';
import AgentCard from '../components/AgentCard';

const AgentsList = () => {
    return (
        <div>
            <h1>Agents</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Agent cards will be rendered here */}
            </div>
        </div>
    );
};

export default AgentsList;
