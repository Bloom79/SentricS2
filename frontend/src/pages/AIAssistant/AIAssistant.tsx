/**
 * AI Assistant Page
 * AI-powered document extraction and conversational assistant
 */

import React, { useState } from 'react';
import {
  Bot,
  Upload,
  FileText,
  Send,
  Brain,
  FileSearch,
  MessageSquare,
  Sparkles,
  Copy,
  Download,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function AIAssistant() {
  const [activeTab, setActiveTab] = useState<'extraction' | 'chat'>('extraction');
  const [inputMessage, setInputMessage] = useState('');
  const [messages] = useState<
    Array<{
      id: string;
      type: 'user' | 'assistant';
      content: string;
      timestamp: string;
    }>
  >([
    {
      id: '1',
      type: 'assistant',
      content:
        'Hello! I am your AI assistant specialized in energy documents. How can I help you today?',
      timestamp: '14:30:00',
    },
  ]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
            <Brain className="h-8 w-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">AI Assistant</h1>
            <p className="text-muted-foreground mt-1">
              Intelligent data extraction and conversational assistance
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        <Button
          variant={activeTab === 'extraction' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('extraction')}
        >
          <FileSearch className="mr-2 h-4 w-4" />
          Document Extraction
        </Button>
        <Button
          variant={activeTab === 'chat' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('chat')}
        >
          <MessageSquare className="mr-2 h-4 w-4" />
          Chat Assistant
        </Button>
      </div>

      {/* Document Extraction Tab */}
      {activeTab === 'extraction' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Upload Area */}
          <div className="lg:col-span-1 space-y-6">
            <div className="border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Upload Documents</h3>
              <div className="border-2 border-dashed border-muted rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer">
                <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
                <p className="text-muted-foreground mb-2">Drag documents here or click to select</p>
                <p className="text-sm text-muted-foreground">
                  PDF, Images, Excel, Word, XML (max 50MB)
                </p>
              </div>
            </div>

            {/* Document List */}
            <div className="border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Recent Documents</h3>
              <div className="space-y-3">
                <div className="p-3 border rounded-lg cursor-pointer hover:bg-muted">
                  <div className="flex items-start gap-3">
                    <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
                    <div className="flex-1">
                      <p className="font-medium text-sm">TICA_SolareVerdi_2024.pdf</p>
                      <p className="text-xs text-muted-foreground">2.4 MB • Completed</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Extracted Data */}
          <div className="lg:col-span-2">
            <div className="border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Extracted Data</h3>
              <div className="text-center py-12 text-muted-foreground">
                Select a document to view extracted data
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chat Tab */}
      {activeTab === 'chat' && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Chat Interface */}
          <div className="lg:col-span-3">
            <div className="border rounded-lg h-[600px] flex flex-col">
              {/* Chat Header */}
              <div className="p-4 border-b">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
                    <Bot className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold">Kronos AI Assistant</h3>
                    <p className="text-sm text-muted-foreground">Online</p>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[70%] rounded-lg p-4 ${
                        message.type === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      <p className="text-xs mt-2 opacity-70">{message.timestamp}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Input */}
              <div className="p-4 border-t">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Type a message..."
                    className="flex-1 px-4 py-2 border rounded-lg"
                    onKeyPress={(e) =>
                      e.key === 'Enter' && inputMessage.trim() && setInputMessage('')
                    }
                  />
                  <Button onClick={() => inputMessage.trim() && setInputMessage('')}>
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Info Panel */}
          <div className="lg:col-span-1 space-y-6">
            <div className="border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">AI Capabilities</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="font-medium">Document Analysis</p>
                  <p className="text-muted-foreground text-xs">
                    Automatic data extraction from PDFs and images
                  </p>
                </div>
                <div>
                  <p className="font-medium">Compliance Check</p>
                  <p className="text-muted-foreground text-xs">
                    Automatic regulatory compliance verification
                  </p>
                </div>
                <div>
                  <p className="font-medium">Deadline Management</p>
                  <p className="text-muted-foreground text-xs">
                    Automatic identification and reminders
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
