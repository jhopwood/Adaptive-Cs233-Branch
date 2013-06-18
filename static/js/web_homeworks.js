if (typeof web_homeworks === 'undefined')
{
    function makefunc(x) {
        return function( ) { return x; }
    }

    web_homeworks = {"data":{}};
    var current_homework = {};

    web_homeworks.init = function() {
        $(document).ready(function() {
            if($("#web_homeworks_container").length == 0)
                $("#tool_container").append('<div id="web_homeworks_container"></div>');
            else
                $("#web_homeworks_container").show();
            // The first thing we want to do is load the index page
            web_homeworks.load_index();
        });
    }

    web_homeworks.load_index = function() {
        var uri = parseUri(window.location.href);
        var magic_number = uri.queryKey['student'];
        $("#web_homeworks_container").html(web_homeworks.index_container_html());
        // Load all of the web homeworks from the database
        $.post("/webhomeworks",{},function(received_json) { 
            var results = JSON.parse(received_json).result;
            var empty = true;
            for(var i = 0 ; i < results.length ; i++) {
                var homework = results[i];
                if(homework.viewable) {
                    $("#web_homeworks_assignments table tbody").append(web_homeworks.index_html_for_homework(homework, magic_number));
                    empty = false;
                }
            }
            if(empty)
                $("#web_homeworks_assignments table tbody").append("<tr><td>There doesn't seem to be anything here!</td></tr>");
        });
    }
    
    web_homeworks.load_homework_page = function(homework, magic_number) {
        $("#web_homeworks_container").html(web_homeworks.homework_container_html(homework));
        if (!homework.viewable) return;
	var problems = homework.problems;
        var ps = new ProblemSet("web_homework_assignment", magic_number, 375);
	current_homework.problem_set = ps;
        for(var i = 0 ; i < problems.length ; i++) {
            var problem = problems[i];
            ps.add(problem.url, problem.id, problem.height);
        }
    }

    web_homeworks.uninit = function() {
        $("#web_homeworks_container").hide();
    }
    
    /*/
     *  HTML Methods
     *  Since these pages are entirely javascript, these methods are here to 
     *  generate HTML in various ways. For small snippets of HTML, I try to 
     *  just write strings. If they are complex objects, I instead use built
     *  in Javascript functions to create the objects and set all of the
     *  attributes. This helps avoid long strings of unreadable HTML.
    /*/
    
    web_homeworks.index_container_html = function() {
        table_classes = "table table-bordered"
        thead = "<thead><tr><th>Assignment</th><th>Date Due</th><th>Completion</th></tr></thead>";
        tbody = "<tbody></tbody>";
        table = '<table class="table table-bordered">'+thead+tbody+'</table>';
        assignments = document.createElement("div");
        $(assignments).attr('id','web_homeworks_assignments');
        $(assignments).append(table);
        return assignments;
    }
    
    web_homeworks.homework_container_html = function(homework) {
        var back_button = '<input type="button" class="btn btn-inverse btn-large back-button" value="Back" onClick="window.location.reload()">'
        return back_button+'<h1 class="inline-block">'+homework.name+"</h1><p>(if you use the help videos, I recommend using YouTube's full screen option)</p>"+'<div id="web_homework_assignment"></div>';
    }

    web_homeworks.completion_bar = function(homework, magic_number, row) {
        td = document.createElement("td");
        div = document.createElement("div");
	$(div).attr('class','progress');
        div2 = document.createElement("div");
	$(div2).attr('class','bar bar-success');
	$(div).append(div2);
        div3 = document.createElement("div");
	$(div3).attr('class','bar bar-danger');
	$(div).append(div3);
	$(td).append(div);
	$(row).append(td); 

	(function() {
	   var g = makefunc({div2:div2, div3:div3, td:td});
           $.post("/assignmentscore", {"student":magic_number, "name":homework.name}, function(received_json) { 
               var complete = JSON.parse(received_json);
	       var my = g();
	       $(my.div2).attr('style','width: '+complete+'%');
	       $(my.div3).attr('style','width: '+(100-complete)+'%');
	       $(my.td).append('<div class="percentage"> ' + complete + '% Complete </div>');
           });
	}());
    }
    
    web_homeworks.index_html_for_homework = function(homework, magic_number) {
        row = document.createElement("tr");
        $(row).attr('class','web_homeworks_assignment');
        $(row).append("<td>"+homework.name+"</td>");
        var date_due = new Date(homework.date_due);
        $(row).append("<td>"+ web_homeworks.format_index_date(date_due) +"</td>"); // 
	web_homeworks.completion_bar(homework, magic_number, row)
        $(row).click(function() {
            //  When they click on a homework, take them to the page to submit
            //  the homework
            web_homeworks.load_homework_page(homework, magic_number);
        });
        return row;
    }

var dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
var monthNames = [ "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ];
    
    web_homeworks.format_index_date = function(date) {
        var ap = "AM";
        var hour = date.getHours();
        if (hour   > 11) { ap = "PM";        }
        if (hour   > 12) { hour = hour - 12; }
        if (hour   == 0) { hour = 12;        }
	var pad = (date.getMinutes() < 10) ? "0" : "";
        return dayNames[date.getDay()]+", "+monthNames[date.getMonth()]+" "+date.getDate()+", "+date.getFullYear()+" at "+hour+":"+pad+date.getMinutes()+" "+ap;
    }
}