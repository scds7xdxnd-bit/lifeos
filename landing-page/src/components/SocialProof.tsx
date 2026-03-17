const SocialProof = () => {
  return (
    <section className="py-20">
      <div className="container mx-auto px-6">
        <h2 className="text-4xl font-bold text-center text-gray-800 mb-8">
          Loved by users
        </h2>
        <div className="flex flex-wrap">
          <div className="w-full md:w-1/3 px-2 mb-4">
            <div className="bg-white rounded-lg p-6 shadow-md">
              <p className="text-gray-600 mb-4">
                "LifeOS has completely changed the way I manage my life. I can't
                imagine going back."
              </p>
              <p className="text-gray-800 font-bold">- Placeholder User</p>
            </div>
          </div>
          <div className="w-full md:w-1/3 px-2 mb-4">
            <div className="bg-white rounded-lg p-6 shadow-md">
              <p className="text-gray-600 mb-4">
                "The insights are incredible. I'm learning so much about
                myself."
              </p>
              <p className="text-gray-800 font-bold">- Another User</p>
            </div>
          </div>
          <div className="w-full md:w-1/3 px-2 mb-4">
            <div className="bg-white rounded-lg p-6 shadow-md">
              <p className="text-gray-600 mb-4">
                "I finally feel like I'm in control of my life. Thank you,
                LifeOS!"
              </p>
              <p className="text-gray-800 font-.bold">- A Happy Customer</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SocialProof;
