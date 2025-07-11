"use client";

import Zenyth from "./svg/Zenyth_simple";


// Define the Header component
function Footer() {
    return (

  <footer className="footer footer-center bg-base-100 text-base-content p-5 w-full [box-shadow:0_-10px_15px_-3px_rgba(0,0,0,0.1),0_-4px_6px_-4px_rgba(0,0,0,0.1)]">
    <aside>
      <Zenyth className="w-20 h-20"/>
      <div className="font-bold text-base-content">
        ZENYTH.
        <br />
        <br />
        <p className="font-nunito font-bold">Got any questions ? Email me at <a href="mailto:mathisgenthon@outlook.fr" className="link text-purple-500">mathisgenthon@outlook.fr</a></p>
      </div>
      
    </aside>
  </footer>

);
}

// Export the component
export default Footer;