const Features = () => {
  return (
    <section className="bg-white py-20">
      <div className="container mx-auto px-6">
        <h2 className="text-4xl font-bold text-center text-gray-800 mb-8">
          Features
        </h2>
        <div className="flex flex-wrap">
          <div className="w-full md:w-1/3 px-2 mb-4">
            <div className="bg-gray-100 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-2">Unified Dashboard</h3>
              <p className="text-gray-600">
                See all your important life data in one place.
              </p>
            </div>
          </div>
          <div className="w-full md:w-1/3 px-2 mb-4">
            <div className="bg-gray-100 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-2">AI-Powered Insights</h3>
              <p className="text-gray-600">
                Get personalized recommendations and insights.
              </p>
            </div>
          </div>
          <div className="w-full md:w-1/3 px-2 mb-4">
            <div className="bg-gray-100 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-2">Track Everything</h3>
              <p className="text-gray-600">
                From your finances to your fitness, track it all.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Features;
