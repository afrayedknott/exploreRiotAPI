# exploreRiotAPI

<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[Contributors][contributors-url]
[Forks][forks-url]
[Stargazers][stars-url]
[Issues][issues-url]
[MIT License][license-url]
[LinkedIn][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/afrayedknott/exploreRiotAPI/">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Riot Games API End-to-End Analytics Pipeline</h3>

  <p align="center">
    Code for pulling data from the Riot Games API and making the data ready for analytics
    <br />
    <a href="https://github.com/afrayedknott/exploreRiotAPI"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/afrayedknott/exploreRiotAPI">View Demo</a>
    ·
    <a href="https://github.com/afrayedknott/exploreRiotAPI/issues">Report Bug</a>
    ·
    <a href="https://github.com/afrayedknott/exploreRiotAPI/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

I am building this end-to-end data pipeline to bring account and match data from the Riot Games Da API to an analyzable state.

Pipeline flow:
* Pull Ranked player profiles to provide seed data as recommended by Riot Games API developers and community members/managers on their Discord.
* Pull match history data based on these profiles.
* Store all the data in a data lake.
* Clean and process data on the way to a data warehouse.
* Live reporting available from a data warehouse.
* Data pulling from data API from a data warehouse.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

* an IDE that can interface with a Python interpreter, ideally, [VS Code](https://code.visualstudio.com/download)
* a Python interpreter ([Win](https://www.python.org/downloads/) or [Mac](https://www.python.org/downloads/macos/))

### Instructions 
<!-- TODO: include images for almost every step -->
1. Install VS Code.
2. Install Python.
3. Open VS Code.
4. Open the Extensions pane, on the left by default, and install the Python extension.
5. Git clone this repo (easiest way is to open the Source Control pane on the left and click "Clone Repository" and paste in the URL "https://github.com/afrayedknott/exploreRiotAPI.git" at the prompt).
6. Open the project repo.
7. Press Ctrl+Shift+P to access the Command Palette (list of preset commands) and search for "Python: Select Interpreter".
8. Select "Python: Select Interpreter" to get a list of Python interpreters and choose the "Recommended" one.
9. Get the config.json file from [Dropbox](https://www.dropbox.com/scl/fi/a8mjl1q4yhbnz3pjm7sug/config.json?rlkey=uw1j8fdjyh0tqdfmw08soo85x&dl=0) and store it in the parent folder of this repo. <!-- TODO: get the files on Dropbox and share properly. -->
   * The API key is only valid for 24 hours. Please message me for a refreshed API key.
   * Replace the API key at the key-value pairing below:
   ```
   api_key: "#ENTER##API####KEY##HERE#"
   ```
10. Run the command below in the Terminal to install all the required modules/packages. The modules/packages listed in the requirements.txt file in the repo will be installed.
   ```
   pip install -r requirements.txt
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of h

ow a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

### Now
- [ ] ReadMe with instructions on how non-Python users can run and test the code
- [ ] Make required files that shouldn't be held in the repo itself (such as config.json and requirements.txt) easily downloadable

### Next
- [ ] Add the next step in the data pipeline of extracting ids from the seed data pull to extract match data
    - [ ] Make it easily runnable from a pre-existing file of seed data so the user can test out this feature without waiting for a fresh pull which could take multiple hours or days
    - [ ] Make it easily swappable to go from non-test mode to test mode

### Later
- [ ] SQL Handler
- [ ] Refactor to pipe all the data pulling and data pushing to a postGres db instead
    - [ ] Utilize the JSONB array functionality of postGres to have a hybrid db

See the [open issues](https://github.com/afrayedknott/exploreRiotAPI/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING 
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>
-->

<!-- LICENSE 
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
-->



## Contact

Eugene Choi - [@afrayedknotty](https://www.threads.net/@afrayedknotty) - eugenechoi86@gmail.com

Project Link: [https://github.com/afrayedknott/exploreRiotAPI](https://github.com/afrayedknott/exploreRiotAPI)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS 
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
* [Malven's Grid Cheatsheet](https://grid.malven.co/)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [React Icons](https://react-icons.github.io/react-icons/search)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

-->

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/afrayedknott/exploreRiotAPI/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/afrayedknott/exploreRiotAPI/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/afrayedknott/exploreRiotAPI/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/afrayedknott/exploreRiotAPI/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/afrayedknott/exploreRiotAPI/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/eugenechoi86/
[product-screenshot]: images/screenshot.png
