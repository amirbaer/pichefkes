// Source: https://www.static-18.themodernnomad.com/wp-content/uploads/2019/01/Audible-ScreenScraperJanuary2019.txt

// How to use.
// Log on to Audible, and open up your library. 
// It can be a good idea to increase the number of items per page
// and the time period you look back.

// Next, you want to run this entire file as a script on the page.
// Chrome, Firefox and Internet Explorer does this differently.
// For chrome, press F12 to open the Chrome Dev Tools, and click 
// on the Console. Then paste in this whole file in the console
// window and press enter.

// But first, set this to true if you want to include the image,
// otherwise leave it. I also suggest you copy and paste the
// table into excel or another spreadsheet application.
var includeImage = false;

// Second, set this to true if you want to include audible shows.
var includeShows = false;

// Helper methods to convert from 2h 15m to 135
var convertToMinutes = function(str) {
  var match = str.match(/.*?(\d+)\s*?h.*?/);
  var hours = (match != null) ? parseInt(match[1]) : 0;
  match = str.match(/.*?(\d+)\s*?m.*?/);
  var minutes = (match != null) ? parseInt(match[1]) : 0;
  return hours * 60 + minutes;
};

// Where we will store our extracted data
var headerRow = [
	$(document.createTextNode('Title')),
	$(document.createTextNode('Author')),
	$(document.createTextNode('Minutes')),
	$(document.createTextNode('Buy Date')),
	$(document.createTextNode('Rating')),
	$(document.createTextNode('Performance')),
	$(document.createTextNode('Story')),
	$(document.createTextNode('Time Left'))];
if(includeImage) headerRow.unshift($(document.createTextNode('Image')));

var tableArray = [headerRow];

// Helper method to extract an author link that works for Excel
var getAuthor = function(row){
	var authorLinks = row.find('td:nth-of-type(3) .bc-list a');
	if(authorLinks.length > 1) {
		var text = row.find('td:nth-of-type(3) .bc-list').text().replace(/\s+/g, " ").trim();
		var target = "/search?searchAuthor=" + encodeURIComponent(text);
		authorLinks = $('<a href="'+target+'">'+text+'</a>');
	} 
	return authorLinks;
};

// Let's fill in the tableArray!
jQuery('tr[class*="adbl-library-row"]').each(function(index){
	var row = $( this );
	
	if(!includeShows) {
		if(row.find('td:nth-of-type(2) .bc-list-item:nth-of-type(2)').text().trim() == "View all episodes") return;
	}
	
	var image = row.find('td:nth-of-type(1) img').clone().attr("width", "90");
	var title = row.find('td:nth-of-type(2) .bc-list-item:nth-of-type(1)').contents();
	var author = getAuthor(row);
	var minutes = $(document.createTextNode(convertToMinutes(row.find('td:nth-of-type(4)').text())));
	var date = $(document.createTextNode(row.find('td:nth-of-type(5)').text()));
	var rating = $(document.createTextNode(row.find('*[data-star-count]:first').attr('data-star-count')));
	var performance = $(document.createTextNode(row.find('*[data-star-count]:eq(1)').attr('data-star-count')));
	var story = $(document.createTextNode(row.find('*[data-star-count]:eq(2)').attr('data-star-count')));
	var minutesleft = $(document.createTextNode(convertToMinutes(row.find('td:nth-of-type(1) .bc-col:nth-of-type(1) .bc-row:nth-of-type(3) ').text().trim().split("\n")[0])));
	
	var result = [title, author, minutes, date, rating, performance, story, minutesleft];
	if(includeImage) result.unshift(image);
	tableArray.push(result);
});

// Function to create a table as a child of el.
// data must be an array of arrays (outer array is rows).
function tableCreate(el, data)
{
    var tbl  = document.createElement("table");
    tbl.style.width  = "70%";
	tbl.border = "1";

    for (var i = 0; i < data.length; ++i)
    {
        var tr = tbl.insertRow();
        for(var j = 0; j < data[i].length; ++j)
        {
            var td = tr.insertCell();
			data[i][j].each(
				function(){
					$(this).clone().appendTo(td);
				});
        }
    }
    el.appendChild(tbl);
}

tableCreate($('body').empty()[0], tableArray);
