const acc = document.getElementsByClassName("accordion");

for (let i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function () {
    this.classList.toggle("active");
    const panel = this.nextElementSibling;
    if (panel.style.display === "block") {
      panel.style.display = "none";
    } else {
      panel.style.display = "block";
    }
  });
}


function launchAR() {
  const vrViewContainer = document.querySelector(".vrview");

  if (vrViewContainer.requestFullscreen) {
    vrViewContainer.requestFullscreen();
  } else if (vrViewContainer.mozRequestFullScreen) { 
    vrViewContainer.mozRequestFullScreen();
  } else if (vrViewContainer.webkitRequestFullscreen) { 
    vrViewContainer.webkitRequestFullscreen();
  } else if (vrViewContainer.msRequestFullscreen) { 
    vrViewContainer.msRequestFullscreen();
  }

  viewer.autoRotate = true;
  viewer.autoRotateSpeed = 0.5;
}

document.getElementById("ar-btn").addEventListener("click", launchAR);