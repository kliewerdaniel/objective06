import React, { useState, useRef, useEffect } from 'react';
import { Button } from '../components/button';
import { Input } from '../components/input';
import { Card } from '../components/card';
import { Badge } from '../components/badge';
import { cn } from '../utils/cn';

interface Message {
  id: string;
  role: 'user' | 'system';
  content: string;
  citations?: { source: string; id: string }[];
  timestamp: string;
}

interface ChatInterfaceProps {
  onSendMessage: (message: string) => Promise<Message>;
  initialMessages?: Message[];
}

export function ChatInterface({ onSendMessage, initialMessages = [] }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userText = input.trim();
    setInput('');
    setLoading(true);
    setMessages(prev => [...prev, { id: `user-${Date.now()}`, role: 'user', content: userText, timestamp: new Date().toISOString() }]);
    try {
      const response = await onSendMessage(userText);
      setMessages(prev => [...prev, response]);
    } catch {
      setMessages(prev => [...prev, { id: `err-${Date.now()}`, role: 'system', content: 'Sorry, I encountered an error processing your request.', timestamp: new Date().toISOString() }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card variant="elevated" className="self-digital-twin">
      <div className="self-digital-twin__messages">
        {messages.map(msg => (
          <div key={msg.id} className={cn('self-digital-twin__message', `self-digital-twin__message--${msg.role}`)}>
            <div className="self-digital-twin__message-role">
              <Badge variant={msg.role === 'user' ? 'primary' : 'secondary'}>{msg.role === 'user' ? 'You' : 'SELF'}</Badge>
              <span className="self-digital-twin__message-time">{new Date(msg.timestamp).toLocaleTimeString()}</span>
            </div>
            <div className="self-digital-twin__message-content">{msg.content}</div>
            {msg.citations && msg.citations.length > 0 && (
              <div className="self-digital-twin__citations">
                {msg.citations.map(c => (
                  <Badge key={c.id} variant="outline">{c.source}</Badge>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="self-digital-twin__typing">SELF is thinking...</div>}
        <div ref={messagesEndRef} />
      </div>
      <div className="self-digital-twin__input">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask about your digital self..."
          disabled={loading}
          suffix={
            <Button variant="primary" size="sm" onClick={handleSend} disabled={loading || !input.trim()}>
              Send
            </Button>
          }
        />
      </div>
    </Card>
  );
}
