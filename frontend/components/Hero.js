"use client";

function Hero() {

  return (
    <div className="hero min-h-screen relative z-0 pt-20 pb-50">
      <div className="hero-content text-neutral-content flex-col lg:flex-row md:flex-row w-full mt-20">

        <div className="max-w-3xl mx-auto">
          <h1 className="animate to-primary font-nunito font-bold leading-[1.05] mb-5 bg-gradient-to-r from-orange-400 bg-clip-text text-transparent lg:text-7xl text-3xl">
            Find your next favorite board game
          </h1>
          <p className="mb-20 text-base-content text-xl font-bold font-nunito">
            Get <a className="dark:text-primary light:text-secondary inline-block font-gloria animate-bounce mx-1"> A.I. </a> powered recommendations based on what you ❤️.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Hero;
