<h1>BookJar</h1>
<h2>Description</h2>

BookJar is a book review website. Users are able to register and log in using their username and password. Once they log in, they can search for books, leave reviews for individual books, and see the reviews made by other people. The site also use  a third-party API by Goodreads, another book review website, to pull in ratings from a broader audience. Finally, users are able to query for book details and book reviews programmatically via BookJar’s API. <a href="https://youtu.be/zCaWgDhzVxQ" target="_blank">Watch a video demo here</a>.<i style="font-size: 12px;"> (Clicking on the link will redirect you to YouTube).</i>

<h2>Back End</h2>
<ul>
  <li>Python - Flask</li>
  <li>PostgreSQL</li>
</ul>
<h2>Front End</h2> (Built for Mobile first)
<ul>
  <li>HTML</li>
  <li>CSS - BootStrap - Flex Box</li>
  <li>Sass</li>
  <li>JavaScript</li>
</ul>
<h3>Sessions and Routing</h3> 
The webpage uses sessions to confirm the user is registered and keep he or she logged in.</br>
Once in, through routing with Flask, and with the use of <strong>JSON</strong> and <strong>JINJA</strong>, the following dynamic functionalities are implemented with Python:
<ul>
  <li><strong>Registration</strong>, users are be able to register for the website, providing a username and password</li>
  <li><strong>Login</strong>, users, once registered, should be able to log in to the website with their username and password</li>
  <li><strong>Logout</strong>, logged in users are able to log out of the site</li>
  <li><strong>Search</strong>, once a user has logged in, they are taken to a page where they can search for a book. Users are able to type in the ISBN number of a book, the title of a book, or the author of a book. After performing the search, the website should display a list of possible matching results, or a message if there were no matches. If the user typed in only part of a title, ISBN, or author name, the search page will find matches for those as well!</li>
  <li><strong>Book Page</strong>, when users click on a book from the results of the search page, they are taken to a book page, with details about the book: its title, author, publication year, ISBN number, and any reviews that users have left for the book on BookJar</li>
  <li><strong>Review Submission</strong>, on the book page, users are able to submit a review: consisting of a rating on a scale of 1 to 5, as well as a text component to the review where the user can write their opinion about a book. Users are only able to submit one review per book</li>
  <li><strong>Goodreads Review Data</strong>, if users make a GET request to the website’s /api/<isbn> route, where <isbn> is an ISBN number, the website will return a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score. The resulting JSON follows the format:
</li>

 ```

{
    "title": "Memory",
    "author": "Doug Lloyd",
    "year": 2015,
    "isbn": "1632168146",
    "review_count": 28,
    "average_score": 5.0
}

 ```
