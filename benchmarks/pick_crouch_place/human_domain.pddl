;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Robot pick crouch place domain
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (domain PICKCROUCHPLACE_HUMAN)
  (:requirements :strips :typing)
  (:types place block)
  (:predicates (robot-at ?p - place)
	       (robot-holding ?b - block)
	       (block-at ?b - block ?p - place)
	       (hand-empty)
	       (hand-tucked)
	       (crouched)
	       )

  (:action move
	     :parameters (?from - place ?to - place)
	     :precondition (and (robot-at ?from))
	     :effect
	     (and (robot-at ?to) (not (robot-at ?from)))
	     )

  (:action tuck
         :parameters ()
	     :precondition (and)
	     :effect
	     (and (hand-tucked))
	     )

  (:action crouch
         :parameters ()
	     :precondition (and)
	     :effect
	     (crouched)
	     )

  (:action pick-up
	     :parameters (?b - block ?loc - place)
	     :precondition (and (block-at ?b ?loc) (robot-at ?loc) (hand-empty))
	     :effect
	     (and (not (hand-empty)) (not (block-at ?b ?loc)) (robot-holding ?b))
	     )

  (:action put-down
        :parameters (?b - block ?loc - place)
        :precondition (and (robot-holding ?b) (robot-at ?loc))
        :effect (and (hand-empty) (not (robot-holding ?b)) (block-at ?b ?loc))
        )
)