import React from 'react'

export default function GenZPricing() {
  const plans = [
    {
      name: "Free Tier",
      price: "$0",
      description: "Perfect for testing and small projects",
      features: [
        "1,000 API calls/month",
        "Basic PII detection",
        "Standard risk assessment",
        "Community support"
      ]
    },
    {
      name: "Pro",
      price: "$49",
      description: "For growing teams and applications",
      features: [
        "100,000 API calls/month",
        "Advanced PII detection & tokenization",
        "Enhanced risk assessment",
        "Priority support",
        "Detailed analytics"
      ]
    },
    {
      name: "Enterprise",
      price: "Custom",
      description: "For large organizations with custom needs",
      features: [
        "Unlimited API calls",
        "Custom PII detection rules",
        "Advanced security features",
        "24/7 dedicated support",
        "Custom integrations",
        "SLA guarantees"
      ]
    }
  ]

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold mb-4">Simple, Transparent Pricing</h2>
        <p className="text-gray-600">Choose the plan that works best for you</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan) => (
          <div key={plan.name} className="bg-white rounded-lg shadow-lg p-8 border border-gray-200 hover:border-blue-500 transition-all">
            <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
            <div className="text-4xl font-bold mb-4">{plan.price}</div>
            <p className="text-gray-600 mb-6">{plan.description}</p>
            <ul className="space-y-3 mb-8">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-center">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>
            <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
              {plan.price === "Custom" ? "Contact Sales" : "Get Started"}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}