
package access

default allow = false

allow {
  input.subject.enterprise == "A"
  input.resource.enterprise == "B"
  input.resource.scope == "read"
  input.context.session_risk < 50
}

obligations := {"timebox": 3600}
