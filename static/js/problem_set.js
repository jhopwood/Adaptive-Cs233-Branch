function ProblemSet(div, student_magic_number, problem_height) {
    this.div = $("#"+div);
    this.div.append('<table style="width: 100%"><thead></thead><tbody></tbody></table>');
    if(problem_height == undefined)
        problem_height = 250;
    this.problem_height = problem_height;
    this.table = $("#"+div+" table");
    this.student = student_magic_number;
    this.problems = [];
    this.onload_handler = function(){};
}

ProblemSet.prototype.onload = function(handler) {
    this.onload_handler = handler;
}

ProblemSet.prototype.add = function(url, problem_id, height, params) {
    var problem = new Problem(this, problem_id, url, params);
    var tr = $(document.createElement("tr"));
    tr.css({width:"100%", height:"100%"});
    var td = $(document.createElement("td"));
    tr.append(td);
    var iframe = problem.iframe(height, this.onload_handler);
    td.append(iframe);
    this.table.append(tr);
    this.problems.push(problem);
}

function Problem(problem_set, problem_id, url, params, height) {
    if (params === undefined)
    params = "";
    this.problem_set = problem_set;
    this.id = problem_id;
    this.params = params;
    this.url = url;
}

Problem.prototype.full_url = function() {
    //  Figure out if the url already has parameters. If it doesnt, we need to add a ? before my parameters.
    //  If it does, then we add a & before my parameters instead
    var delimiter = "?";
    //  If there is a ? in the URL
    if(this.url.indexOf('?') != -1)
    delimiter = "&";
    return this.url+delimiter+"problem_id="+this.id+"&student="+this.problem_set.student+$.param(this.params);
}

Problem.prototype.iframe = function(height, onload_handler) {
    var iframe = $(document.createElement("iframe"));
    iframe.addClass("problem");
    iframe.css({width:"100%", height:height+"px"});
    iframe.attr('scrolling', 'auto');
    iframe.attr('src', this.full_url());
    var url = this.url, problem_id = this.id;
    iframe.load(function() {
        onload_handler(url, problem_id,iframe);
    });
    return iframe;
}