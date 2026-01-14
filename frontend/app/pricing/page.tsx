'use client';

import { useState } from 'react';
import { Check, X, Star, Zap, Users, Shield } from 'lucide-react';

const plans = [
  {
    id: 'free',
    name: 'Free',
    price: { monthly: 0, yearly: 0 },
    description: 'Perfect for trying out Align',
    icon: Star,
    features: [
      '5 mockups per month',
      'Basic AI generation',
      'Chrome extension',
      'Community support',
      'Export to HTML'
    ],
    limitations: [
      'No voice input/output',
      'No collaboration',
      'No version history',
      'No API access'
    ],
    cta: 'Get Started Free',
    popular: false
  },
  {
    id: 'pro',
    name: 'Pro',
    price: { monthly: 19, yearly: 190 },
    description: 'For individual designers and developers',
    icon: Zap,
    features: [
      'Unlimited mockups',
      'Advanced AI models',
      'Voice input/output',
      'Export to Figma/Sketch',
      'Version history',
      'Priority support',
      'Custom voice training',
      'Advanced templates'
    ],
    limitations: [
      'Single user only',
      'Limited collaboration (5 sessions)',
      'No team features'
    ],
    cta: 'Start Pro Trial',
    popular: true
  },
  {
    id: 'team',
    name: 'Team',
    price: { monthly: 49, yearly: 490 },
    description: 'For design teams and agencies',
    icon: Users,
    features: [
      'Everything in Pro',
      'Real-time collaboration',
      'Team workspaces',
      'Admin controls',
      'API access (50k calls/month)',
      'Custom branding',
      'Team analytics',
      'Shared component library',
      'Up to 10 team members'
    ],
    limitations: [
      'No SSO integration',
      'No on-premise deployment'
    ],
    cta: 'Start Team Trial',
    popular: false
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: { monthly: 99, yearly: 990 },
    description: 'For large organizations',
    icon: Shield,
    features: [
      'Everything in Team',
      'SSO integration',
      'Advanced security',
      'Custom plugins',
      'Dedicated support',
      'On-premise deployment',
      'Unlimited API calls',
      'Custom AI model training',
      'Unlimited team members',
      'SLA guarantee'
    ],
    limitations: [],
    cta: 'Contact Sales',
    popular: false
  }
];

const faqs = [
  {
    question: 'How does the AI mockup generation work?',
    answer: 'Align uses advanced AI models (including GPT-4 and Gemini) to analyze your screenshots and natural language descriptions, then generates HTML/CSS mockups that match your requirements.'
  },
  {
    question: 'Can I cancel my subscription anytime?',
    answer: 'Yes, you can cancel your subscription at any time. Your account will remain active until the end of your current billing period.'
  },
  {
    question: 'Do you offer refunds?',
    answer: 'We offer a 14-day free trial for all paid plans. If you\'re not satisfied within the first 30 days, we offer a full refund.'
  },
  {
    question: 'How does team collaboration work?',
    answer: 'Team members can collaborate in real-time on mockups, leave comments, and sync changes across devices. All team activity is tracked and versioned.'
  },
  {
    question: 'Is my data secure?',
    answer: 'Yes, we use enterprise-grade security with encryption in transit and at rest. We\'re SOC2 compliant and never store your data longer than necessary.'
  },
  {
    question: 'Can I integrate Align with other tools?',
    answer: 'Yes, we offer API access and integrations with popular design tools like Figma, Sketch, and Adobe XD. Custom integrations are available for Enterprise customers.'
  }
];

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const handlePlanSelect = (planId: string) => {
    if (planId === 'free') {
      // Redirect to signup
      window.location.href = '/signup?plan=free';
    } else if (planId === 'enterprise') {
      // Open contact form
      window.location.href = '/contact?plan=enterprise';
    } else {
      // Redirect to checkout
      window.location.href = `/checkout?plan=${planId}&billing=${billingCycle}`;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Simple, Transparent Pricing
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Choose the perfect plan for your design workflow
            </p>
            
            {/* Billing Toggle */}
            <div className="flex items-center justify-center mb-8">
              <span className={`mr-3 ${billingCycle === 'monthly' ? 'text-gray-900' : 'text-gray-500'}`}>
                Monthly
              </span>
              <button
                onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
                className="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
              <span className={`ml-3 ${billingCycle === 'yearly' ? 'text-gray-900' : 'text-gray-500'}`}>
                Yearly
              </span>
              {billingCycle === 'yearly' && (
                <span className="ml-2 bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                  Save 17%
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {plans.map((plan) => {
            const Icon = plan.icon;
            const price = plan.price[billingCycle];
            
            return (
              <div
                key={plan.id}
                className={`relative bg-white rounded-2xl shadow-lg border-2 transition-all hover:shadow-xl ${
                  plan.popular ? 'border-blue-500 scale-105' : 'border-gray-200'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <div className="p-8">
                  {/* Plan Header */}
                  <div className="text-center mb-6">
                    <Icon className="h-12 w-12 text-blue-500 mx-auto mb-4" />
                    <h3 className="text-2xl font-bold text-gray-900">{plan.name}</h3>
                    <p className="text-gray-600 mt-2">{plan.description}</p>
                  </div>

                  {/* Price */}
                  <div className="text-center mb-6">
                    <div className="flex items-baseline justify-center">
                      <span className="text-4xl font-bold text-gray-900">${price}</span>
                      {price > 0 && (
                        <span className="text-gray-600 ml-1">
                          /{billingCycle === 'monthly' ? 'month' : 'year'}
                        </span>
                      )}
                    </div>
                    {billingCycle === 'yearly' && price > 0 && (
                      <p className="text-sm text-gray-500 mt-1">
                        ${Math.round(price / 12)}/month billed annually
                      </p>
                    )}
                  </div>

                  {/* Features */}
                  <div className="mb-6">
                    <h4 className="font-semibold text-gray-900 mb-3">What's included:</h4>
                    <ul className="space-y-2">
                      {plan.features.map((feature, index) => (
                        <li key={index} className="flex items-start">
                          <Check className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-600 text-sm">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Limitations */}
                  {plan.limitations.length > 0 && (
                    <div className="mb-6">
                      <h4 className="font-semibold text-gray-900 mb-3">Limitations:</h4>
                      <ul className="space-y-2">
                        {plan.limitations.map((limitation, index) => (
                          <li key={index} className="flex items-start">
                            <X className="h-5 w-5 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-500 text-sm">{limitation}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* CTA Button */}
                  <button
                    onClick={() => handlePlanSelect(plan.id)}
                    className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
                      plan.popular
                        ? 'bg-blue-500 text-white hover:bg-blue-600'
                        : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                    }`}
                  >
                    {plan.cta}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Feature Comparison */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Compare All Features
            </h2>
            <p className="text-gray-600">
              See exactly what's included in each plan
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-4 px-6 font-semibold text-gray-900">Features</th>
                  {plans.map((plan) => (
                    <th key={plan.id} className="text-center py-4 px-6 font-semibold text-gray-900">
                      {plan.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  { feature: 'Mockups per month', values: ['5', 'Unlimited', 'Unlimited', 'Unlimited'] },
                  { feature: 'AI models', values: ['Basic', 'Advanced', 'Advanced', 'Custom'] },
                  { feature: 'Voice input/output', values: ['✗', '✓', '✓', '✓'] },
                  { feature: 'Real-time collaboration', values: ['✗', 'Limited', '✓', '✓'] },
                  { feature: 'API access', values: ['✗', '✗', '50k calls', 'Unlimited'] },
                  { feature: 'Team members', values: ['1', '1', '10', 'Unlimited'] },
                  { feature: 'SSO integration', values: ['✗', '✗', '✗', '✓'] },
                  { feature: 'On-premise deployment', values: ['✗', '✗', '✗', '✓'] },
                  { feature: 'Support', values: ['Community', 'Priority', 'Priority', 'Dedicated'] }
                ].map((row, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50">
                    <td className="py-4 px-6 font-medium text-gray-900">{row.feature}</td>
                    {row.values.map((value, valueIndex) => (
                      <td key={valueIndex} className="py-4 px-6 text-center text-gray-600">
                        {value}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-gray-600">
              Everything you need to know about Align pricing
            </p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div key={index} className="bg-white rounded-lg shadow">
                <button
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                  className="w-full text-left py-4 px-6 font-semibold text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  <div className="flex justify-between items-center">
                    <span>{faq.question}</span>
                    <span className="text-gray-400">
                      {openFaq === index ? '−' : '+'}
                    </span>
                  </div>
                </button>
                {openFaq === index && (
                  <div className="px-6 pb-4">
                    <p className="text-gray-600">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-blue-600 py-16">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Your Design Workflow?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of designers and developers using Align to create better mockups faster.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => handlePlanSelect('free')}
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              Start Free Trial
            </button>
            <button
              onClick={() => handlePlanSelect('enterprise')}
              className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
            >
              Contact Sales
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}