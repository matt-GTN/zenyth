"use client";
import Woman from "@/components/svg/Woman_hero";
function Hero() {

  return (
    <div className="hero relative w-full max-w-4xl z-0">
      <div className="hero-content text-neutral-content flex-col lg:flex-row md:flex-row w-full mt-10">
        <Woman width={300} height={200} />

        <div className="mx-auto">
          <h1 className="animate to-purple-500 font-nunito font-bold leading-[1.05] bg-gradient-to-r from-orange-400 bg-clip-text text-transparent text-3xl pl-5 lg:text-4xl max-w-2xl">
            Summarize Youtube Videos and save hours of your time
          </h1>
        </div>
      </div>
    </div>
  );
}

export default Hero;
