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

// Helper methods to convert from 'Released: 05-05-04' to '05-05-04' (MM-DD-YY)
var extractReleasedDate = function(str) {
  var match = str.match(/.*?(\d+-\d+-\d+).*?/);
  var date = (match != null) ? match[1] : 0;
  return date;
}

// Where we will store our extracted data
var headerRow = [
	$(document.createTextNode('Title')),
	$(document.createTextNode('Author')),
	$(document.createTextNode('Minutes')),
	$(document.createTextNode('Date Added')),
	$(document.createTextNode('Date Released'))];
if(includeImage) headerRow.unshift($(document.createTextNode('Image')));

var tableArray = [headerRow];

// Helper method to extract an author link that works for Excel
var getAuthor = function(row){
	var authorLinks = row.find('td:nth-of-type(3) .bc-row');
	if(authorLinks.length > 1) {
		var text = row.find('td:nth-of-type(3) .bc-list').text().replace(/\s+/g, " ").trim();
		var target = "/search?searchAuthor=" + encodeURIComponent(text);
		authorLinks = $('<a href="'+target+'">'+text+'</a>');
	} 
	return authorLinks;
};

// Let's fill in the tableArray!
jQuery('tr[class*="bc-table-row"]').each(function(index){
	if (index == 0) {
		return;
	}

	var row = $( this );

	var image = row.find('td:nth-of-type(1) img').clone().attr("width", "90");
	var title = row.find('td:nth-of-type(2) .bc-list-item:nth-of-type(1)').contents();
	var author = row.find('td:nth-of-type(3) .bc-row:nth-of-type(1)').contents();
	var minutes = $(document.createTextNode(convertToMinutes(row.find('td:nth-of-type(2) .bc-list-item:nth-of-type(3) .bc-text:nth-of-type(1)').text())));
	var date_added = $(document.createTextNode(row.find('td:nth-of-type(5)').text()));
	var date_released = $(document.createTextNode(extractReleasedDate(row.find('td:nth-of-type(2) .bc-list-item:nth-of-type(4) .bc-text:nth-of-type(1)').text())));
	
	var result = [title, author, minutes, date_added, date_released];
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