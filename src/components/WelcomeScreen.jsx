import React from 'react';
import { Sparkles, MessageSquare, Brain, Upload, Zap } from 'lucide-react';

const WelcomeScreen = ({ documents }) => {
  const features = [
    {
      icon: MessageSquare,
      title: 'Smart Q&A',
      description: 'Ask questions and get precise answers from your documents',
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      icon: Brain,
      title: 'Mind Maps',
      description: 'Visualize document relationships with interactive diagrams',
      gradient: 'from-purple-500 to-pink-500'
    },
    {
      icon: Zap,
      title: 'Instant Analysis',
      description: 'Real-time processing with AI-powered insights',
      gradient: 'from-orange-500 to-red-500'
    }
  ];

  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="max-w-3xl w-full">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl mb-6">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-purple-500 to-pink-500 bg-clip-text text-transparent">
            Welcome to DocuMind
          </h1>
          <p className="text-lg text-light-textSecondary dark:text-dark-textSecondary max-w-2xl mx-auto">
            Your intelligent document assistant powered by advanced AI. Upload documents and start asking questions to unlock insights.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="p-6 bg-light-sidebar dark:bg-dark-sidebar rounded-2xl border border-light-border dark:border-dark-border hover:border-purple-500/50 transition-all group"
            >
              <div className={`w-12 h-12 bg-gradient-to-br ${feature.gradient} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold mb-2">{feature.title}</h3>
              <p className="text-sm text-light-textSecondary dark:text-dark-textSecondary">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <div className="text-center p-6 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-2xl border border-purple-500/20">
          <Upload className="w-8 h-8 mx-auto mb-3 text-purple-500" />
          <h3 className="font-semibold mb-2">Get Started</h3>
          <p className="text-sm text-light-textSecondary dark:text-dark-textSecondary">
            {documents.length === 0 
              ? 'Upload your first document to begin your AI-powered analysis'
              : `${documents.length} document${documents.length > 1 ? 's' : ''} ready. Start asking questions!`
            }
          </p>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;
