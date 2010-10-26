// vim: set ts=2 sts=2 et sw=2:


(function($){
    $.fn.boxWithLabel = function(args) {
      args.type = args.type || "checkbox";

      var box = $(this);
      var button = $("<input></input>")
        .attr("type", args.type)
        .appendTo(box);
      if(typeof(args.value) != undefined) {
        button.val(args.value);
      }
      if(args.checked) {
        button.attr("checked", "checked");
      }
      var lbl = $("<a></a>")
        .attr("href", "#")
        .html(args.label)
        .appendTo(box);

      // Events
      lbl.click(function() {
          button.click();
          return false;
        });
      if(args.click) {
        button.click(args.click);
      }

      return box;
    };

    $.log = function(message) {
      if(window.console) {
        console.debug(message);
      } else {
        alert(message);
      }
    };

  })(jQuery);