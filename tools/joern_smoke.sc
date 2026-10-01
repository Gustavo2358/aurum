import io.shiftleft.semanticcpg.language.*
import io.joern.dataflowengineoss.language.*
import io.shiftleft.codepropertygraph.generated.nodes.*

@main def inspect(cpgFile: String, out: String) = {
  importCpg(cpgFile)
  val methods = cpg.method.filterNot(_.isExternal).filterNot(_.name == "<global>").l
  val inventory = methods.map { m =>
    ujson.Obj("name" -> m.name, "file" -> m.filename,
      "line" -> m.lineNumber.getOrElse(-1), "line_end" -> m.lineNumberEnd.getOrElse(-1),
      "cfg_nodes" -> m.cfgNode.size,
      "calls" -> ujson.Arr.from(m.call.map(c => ujson.Obj("name" -> c.name,
        "line" -> c.lineNumber.getOrElse(-1), "callees" -> ujson.Arr.from(c.callee.name.l))).l))
  }
  val selections = List(
    ("authorization", "authorize_apply", "credit_admission", "price.principal"),
    ("capture", "capture_apply", "cumulative_delta", "c->principal"),
    ("refund", "refund_apply", "cumulative_delta", "c->principal"),
    ("billing", "invoice_minimum", "ceil_rate", "total"),
    ("payment", "pay_apply", "project_account", "e")
  )
  val sentinels = selections.map { case (label, method, callee, argument) =>
    val m = cpg.method.nameExact(method).head
    val calls = m.call.nameExact(callee).l
    val sinks = calls.flatMap(_.argument.filter(_.code.contains(argument)).l)
    val sources = m.parameter.l
    val flows = sinks.iterator.reachableByFlows(sources.iterator).l
    ujson.Obj("id" -> label, "method" -> method, "call" -> callee,
      "cross_file_callees" -> ujson.Arr.from(calls.flatMap(_.callee.filterNot(_.isExternal).map(_.filename).l)),
      "sink_lines" -> ujson.Arr.from(sinks.map(_.lineNumber.getOrElse(-1))),
      "controls" -> ujson.Arr.from(m.controlStructure.map(x => ujson.Obj("line" -> x.lineNumber.getOrElse(-1), "code" -> x.code)).l),
      "writes" -> ujson.Arr.from(m.call.nameExact("<operator>.assignment").map(x => ujson.Obj("line" -> x.lineNumber.getOrElse(-1), "code" -> x.code)).l),
      "control_dependencies" -> ujson.Arr.from(m.call.controlledBy.dedup.map(x => ujson.Obj("line" -> x.lineNumber.getOrElse(-1), "code" -> x.code)).l),
      "parameter_to_argument_paths" -> flows.size,
      "path_samples" -> ujson.Arr.from(flows.take(2).map(p => ujson.Arr.from(p.elements.map(n => ujson.Obj("code" -> n.code,"line" -> n.lineNumber.getOrElse(-1)))))))
  }
  val output = ujson.Obj("methods" -> ujson.Arr.from(inventory), "sentinels" -> ujson.Arr.from(sentinels),
    "files" -> ujson.Arr.from(cpg.file.name.l), "metadata" -> ujson.Arr.from(cpg.metaData.map(_.toString).l))
  java.nio.file.Files.writeString(java.nio.file.Paths.get(out), ujson.write(output,indent=2))
}
