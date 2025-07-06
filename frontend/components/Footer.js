"use client";

import Sophia from "./svg/Zenyth_simple";


// Define the Header component
function Footer() {
    return (

  <footer className="footer footer-center bg-base-100 text-base-content p-10 w-full">
    <aside>
      <Sophia className="w-20 h-20 text-base-content"/>
      <p className="font-bold">
        ZENYTH.
        <br />
        <a className="font-nunito">Earning you hours since 2025</a>
      </p>
      <p>Copyright © {new Date().getFullYear()} - All rights reserved</p>
    </aside>
  </footer>

);
}

// Export the component
export default Footer;