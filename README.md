# Readme
please unzip the movie_details.zip


# Link to GitHub repo for the final project code: 
https://github.com/SUNRUOWEI/Ruowei-Sun.git

# Required Python packages:
requests
bs4 - BeautifulSoup
flask, flask_bootstrap, render_template, request, pandas, matploblib, scikit-learn

# Data sources:
Web Crawler
Get JSON file by crawling the top 250 movie data rated by users in the 
https://m.imdb.com/chart/top/?ref_=nv_mv_250. 
With the help of BeautifulSoup, we selected the data we need by the elements from the web page.
And we used python to store the data into the .json file, which can be used later.

To initiate the web application, execute the app.py file in the Command Prompt (CMD), and then navigate to the website http://127.0.0.1:5000/ using a web browser. This serves as the welcoming interface for the "Top 250 Movies Analyses" website. Users are prompted to complete the form by filling in the required fields and selecting options based on their preferences for movie-related information. Upon form submission, the gathered information acts as filtering criteria, producing personalized results on the page http://127.0.0.1:5000/result/.

The web application consists of two main parts. The first allows users to view graphs and tables related to movie data. The second allows users to enter movie information and see predicted values for the movie's popularity.
