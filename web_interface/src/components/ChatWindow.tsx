import React from 'react';

const ChatWindow = () => {
    return (
        <div className="bg-white rounded-lg shadow-md">
            <div className="p-4 border-b">
                <h2 className="text-xl font-bold">Chat</h2>
            </div>
            <div className="p-4 h-96 overflow-y-auto">
                {/* Chat messages will be rendered here */}
            </div>
            <div className="p-4 border-t">
                <input
                    type="text"
                    placeholder="Type your message..."
                    className="w-full px-3 py-2 border rounded-lg"
                />
            </div>
        </div>
    );
};

export default ChatWindow;
