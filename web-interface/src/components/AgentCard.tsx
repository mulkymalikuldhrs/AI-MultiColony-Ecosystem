import React from 'react';

const AgentCard = ({ agent }) => {
    return (
        <div className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-xl font-bold">{agent.name}</h2>
            <p className="text-gray-500">{agent.description}</p>
        </div>
    );
};

export default AgentCard;
